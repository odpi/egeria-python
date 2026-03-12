# Link Term-Term Relationship
>	Links or unlinks two glossary terms via a typed semantic relationship (e.g. Synonym, Antonym, PreferredTerm, TranslationOf).

# Required

## Term 1
>	**Input Required**: True

>	**Description**: The name of the first term to connect.


## Term 2
>	**Input Required**: True

>	**Description**: The name of the second term to connect.


## Relationship Type
>	**Input Required**: True

>	**Description**: The type of relationship connecting the two terms. E.g. Synonym, Antonym, PreferredTerm, ReplacedByTerm, TranslationOf, etc.

>	**Valid Values**: RelatedTerm,Synonym,Antonym,PreferredTerm,ReplacementTerm,Translation,IsA,ValidValue


# Link Term-Term Relationship Properties

## Label
>	**Input Required**: False

>	**Description**: A label used to identify or categorise a relationship link.


## Expression
>	**Input Required**: False

>	**Description**: An expression describing a membership, relationship or classification.


## Term Status
>	**Input Required**: False

>	**Description**: The status of the term-term relationship.

>	**Valid Values**: DRAFT,ACTIVE,DEPRECATED,OBSOLETE,OTHER

>	**Default Value**: ACTIVE


## Source
>	**Input Required**: False

>	**Description**: The source of the information.


# Common Properties

## Description
>	**Input Required**: False

>	**Description**: A description.

