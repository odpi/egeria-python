# Link Term-Term Relationship
> Links or unlinks two glossary terms via a typed semantic relationship (e.g. Synonym, Antonym, PreferredTerm, TranslationOf).

## Relationship Type
>	**Input Required**: True

>	**Attribute Type**: Valid Value

>	**Description**: The type of relationship connecting the two terms. E.g. Synonym, Antonym, PreferredTerm, ReplacedByTerm, TranslationOf, etc.

>	**Valid Values**: RelatedTerm,Synonym,Antonym,PreferredTerm,ReplacementTerm,Translation,IsA,ValidValue


## Term 1
>	**Input Required**: True

>	**Attribute Type**: Reference Name

>	**Description**: The name of the first term to connect.


## Term 2
>	**Input Required**: True

>	**Attribute Type**: Reference Name

>	**Description**: The name of the second term to connect.


## Label
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: A label used to identify or categorise a relationship link.

>	**Alternative Labels**: Wire Label


## Expression
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: An expression describing a membership, relationship or classification.


## Source
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: The source of the information.


## Term Status
>	**Input Required**: False

>	**Attribute Type**: Valid Value

>	**Description**: The status of the term-term relationship.

>	**Valid Values**: DRAFT,ACTIVE,DEPRECATED,OBSOLETE,OTHER

>	**Default Value**: ACTIVE


## Journal Entry
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: A text entry into a journal.


## Description
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: A description.

