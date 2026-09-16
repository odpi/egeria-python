___

## Link Control Flow
> Create a ControlFlow lineage relationship between two elements.

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
