___

## Update Control Flow
> Update the properties of an existing ControlFlow lineage relationship, identified by its own relationship GUID.

### Lineage Relationship
>	**Input Required**: True

>	**Attribute Type**: Simple

>	**Description**: The GUID of the lineage relationship, as returned when it was linked (a Link <Type> command's output).


### Label
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: A label used to identify or categorise a relationship link.

>	**Alternative Labels**: Wire Label


### Description
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: A description.


### Guard
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: Informational value passed to the process step; the step's behaviour may vary depending on the guard it receives.


### Mandatory Guard
>	**Input Required**: False

>	**Attribute Type**: Bool

>	**Description**: Whether this guard must be present for the step to be actioned.

>	**Default Value**: false


### ISC Qualified Name
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: Qualified name of the Information Supply Chain this lineage relationship belongs to, if any.


___
