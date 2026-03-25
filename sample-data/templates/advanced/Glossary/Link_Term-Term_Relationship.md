# Link Term-Term Relationship
> Links or unlinks two glossary terms via a typed semantic relationship (e.g. Synonym, Antonym, PreferredTerm, TranslationOf).

## Term 1
>	**Input Required**: True

>	**Attribute Type**: Reference Name

>	**Description**: The name of the first term to connect.


## Term 2
>	**Input Required**: True

>	**Attribute Type**: Reference Name

>	**Description**: The name of the second term to connect.


## Relationship Type
>	**Input Required**: True

>	**Attribute Type**: Valid Value

>	**Description**: The type of relationship connecting the two terms. E.g. Synonym, Antonym, PreferredTerm, ReplacedByTerm, TranslationOf, etc.

>	**Valid Values**: RelatedTerm,Synonym,Antonym,PreferredTerm,ReplacementTerm,Translation,IsA,ValidValue


## Label
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: A label used to identify or categorise a relationship link.

>	**Alternative Labels**: Wire Label


## Expression
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: An expression describing a membership, relationship or classification.


## Term Status
>	**Input Required**: False

>	**Attribute Type**: Valid Value

>	**Description**: The status of the term-term relationship.

>	**Valid Values**: DRAFT,ACTIVE,DEPRECATED,OBSOLETE,OTHER

>	**Default Value**: ACTIVE


## Source
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: The source of the information.


## Journal Entry
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: A text entry into a journal.


## Description
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: A description.


## Effective From
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: The beginning of when an element is viewable.


## Effective Time
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: The time at which an element must be effective in order to be returned by the request.


## Effective To
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: The ending time at which an element is visible.


## External Source GUID
>	**Input Required**: False

>	**Attribute Type**: GUID

>	**Description**: The unique identifier of an external source.


## External Source Name
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: The name of an external source


## For Duplicate Processing
>	**Input Required**: False

>	**Attribute Type**: Bool

>	**Description**: Flag indicating if the request is to support duplicate processing.


## For Lineage
>	**Input Required**: False

>	**Attribute Type**: Bool

>	**Description**: Flag indicating if the request is to support lineage.


## Request ID
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: A user provided or system generated request id for a conversation.


## Confidence
>	**Input Required**: False

>	**Attribute Type**: Simple Int

>	**Description**: A percent confidence in the proposed adding of the member.


## Steward
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: The identifier of the steward responsible for the element.

