# Link Information Supply Chain Child
> Links or unlinks an information supply chain child segment to an Information Supply Chain using CollectionMembership.

## ISC Child
>	**Input Required**: True

>	**Attribute Type**: Reference Name

>	**Description**: A Referenceable that is a logical child of the information supply chain segment.


## ISC Parent
>	**Input Required**: True

>	**Attribute Type**: Reference Name

>	**Description**: A Referenceable that is a logical source or destination for the information supply chain segment.


## Label
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: A label used to identify or categorise a relationship link.

>	**Alternative Labels**: Wire Label


## Membership Rationale
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: Rationale for membership.


## Membership Status
>	**Input Required**: False

>	**Attribute Type**: Valid Value

>	**Description**: The status of adding a member to a collection.

>	**Valid Values**: UNKNOWN,DISCOVERED,PROPOSED,IMPORTED,VALIDATED,DEPRECATED,OBSOLETE,OTHER

>	**Default Value**: PROPOSED


## Notes
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: Notes and observations about the element.


## Journal Entry
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: A text entry into a journal.


## Description
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: A description.

