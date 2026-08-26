___

## Detach Term as Context
> Removes the UsedInContext relationship between a glossary term and the referenceable it provides context for.
>
>	**Alternative Names**: Detach Used in Context

### Term 1
>	**Input Required**: True

>	**Attribute Type**: Reference Name

>	**Description**: The name of the first term to connect.

>	**Alternative Labels**: Term; Term Name


### Element Id
>	**Input Required**: True

>	**Attribute Type**: Reference Name

>	**Description**: The unique identifier (qualified name or GUID) of the element being referenced.

>	**Alternative Labels**: Element Name; Member Id


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
