___

## Link Term-Term Relationship
> Links or unlinks two glossary terms via a typed semantic relationship (e.g. Synonym, Antonym, PreferredTerm, TranslationOf).
>
>	**Alternative Names**: Term-Term Relationship; Term to Term Relationship

### Relationship Type
>	**Input Required**: True

>	**Attribute Type**: Enum

>	**Description**: The type of relationship connecting the two terms. E.g. Synonym, Antonym, PreferredTerm, ReplacedByTerm, TranslationOf, etc.

>	**Valid Values**: RelatedTerm,Synonym,Antonym,PreferredTerm,ReplacementTerm,Translation,ISA,ValidValue,ISARelationship,TermHASARelationship,TYPED BY,TermTYPEDBYRelationship,TYPE OF,TermISATYPEOFRelationship


### Confidence
>	**Input Required**: False

>	**Attribute Type**: Simple Int

>	**Description**: A percent confidence in the proposed adding of the member.


### Expression
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: An expression describing a membership, relationship or classification.


### Source
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: The source of the information.


### Steward
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: The identifier of the steward responsible for the element.


### Term Relationship Status
>	**Input Required**: False

>	**Attribute Type**: Valid Value

>	**Description**: The status of the term-term relationship.

>	**Valid Values**: DRAFT,ACTIVE,DEPRECATED,OBSOLETE,OTHER

>	**Default Value**: ACTIVE


### Effective Time
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: An ISO-8601 string representing the time to use for evaluating effectivity of the elements related to this one.


### Effective From
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: A string in ISO-8601 format that defines the when an element becomes effective (visible).


### Effective To
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: A string in ISO-8601 format that defines the when an element is no longer effective (visible).


___
