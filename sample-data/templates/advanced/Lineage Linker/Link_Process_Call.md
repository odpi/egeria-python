___

## Link Process Call
> Create a ProcessCall lineage relationship between two elements.

### Element One
>	**Input Required**: True

>	**Attribute Type**: Reference Name

>	**Description**: Qualified name, display name, or GUID of the element at end one of the lineage relationship.


### Element Two
>	**Input Required**: True

>	**Attribute Type**: Reference Name

>	**Description**: Qualified name, display name, or GUID of the element at end two of the lineage relationship.


### Label
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: A label used to identify or categorise a relationship link.

>	**Alternative Labels**: Wire Label


### Integration Style
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: The integration style of the information supply chain (e.g. how data flows between segments).


### Data Exchanged
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: The data exchanged in an interaction.


### Description
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: A description.


### Protocol
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: Name of the protocol used for interaction.


### One Way
>	**Input Required**: False

>	**Attribute Type**: Bool

>	**Description**: Is the link one way or bi-directional?

>	**Alternative Labels**: Unidirectional

>	**Default Value**: True


### Frequency
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: A frequency of interaction.


### ISC Qualified Name
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: Qualified name of the Information Supply Chain this lineage relationship belongs to, if any.


### Formula
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: The logic implemented by this process, expressed in the language of the business rather than any one implementation language.


### Formula Type
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: The specification language used to express the Formula (e.g. SQL, Python, natural language).


### Line Number
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: Line number in the source code where this process call is made (ProcessCall only).


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
