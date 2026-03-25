# Attach Collection to Resource
> Connect an existing collection to an element using the ResourceList relationship.
>
>	**Alternative Names**: Collection to Resource

## Element Id
>	**Input Required**: False

>	**Attribute Type**: Reference Name

>	**Description**: The unique identifier (qualified name or GUID) of the element being referenced.

>	**Alternative Labels**: Element Name


## Resource Description
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: Description of the resource or how it is being used. From the ResourceList relationship (0019).


## Resource Id
>	**Input Required**: False

>	**Attribute Type**: Reference Name

>	**Description**: The unique identifier (qualified name or GUID) of the supporting resource in a ResourceList relationship.


## Resource Properties
>	**Input Required**: False

>	**Attribute Type**: Dictionary

>	**Description**: Additional properties needed to use the resource. From the ResourceList relationship (0019).


## Resource Use
>	**Input Required**: False

>	**Attribute Type**: Valid Value

>	**Description**: Describes how the resource is being used. From the ResourceList relationship (0019).


## Watch Resource
>	**Input Required**: False

>	**Attribute Type**: Bool

>	**Description**: Whether the parent entity should receive notifications about changes to this resource. From the ResourceList relationship (0019).


## Collection Id
>	**Input Required**: False

>	**Attribute Type**: Reference Name

>	**Description**: The unique identifier (qualified name or GUID) of the collection.


## Element Id
>	**Input Required**: False

>	**Attribute Type**: Reference Name

>	**Description**: The unique identifier (qualified name or GUID) of the element being referenced.

>	**Alternative Labels**: Element Name


## Effective Time
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: An ISO-8601 string representing the time to use for evaluating effectivity of the elements related to this one.


## Effective From
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: A string in ISO-8601 format that defines the when an element becomes effective (visible).


## Effective To
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: A string in ISO-8601 format that defines the when an element is no longer effective (visible).

