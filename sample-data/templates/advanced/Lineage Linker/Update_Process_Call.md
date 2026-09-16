___

## Update Process Call
> Update the properties of an existing ProcessCall lineage relationship, identified by its own relationship GUID.

### Lineage Relationship
>	**Input Required**: True

>	**Attribute Type**: Simple

>	**Description**: The GUID of the lineage relationship, as returned when it was linked (a Link <Type> command's output).


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


___
