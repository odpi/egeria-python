___

## Link Instances
> Create a relationship between two metadata elements. Not deduplicated: running it twice may create two relationships.

### Relationship Type Name
>	**Input Required**: True

>	**Attribute Type**: Simple

>	**Description**: Open metadata type name of the relationship to create.


### Element 1 GUID
>	**Input Required**: True

>	**Attribute Type**: GUID

>	**Description**: GUID of the element at end 1 of the relationship.


### Element 2 GUID
>	**Input Required**: True

>	**Attribute Type**: GUID

>	**Description**: GUID of the element at end 2 of the relationship.


### Relationship Properties
>	**Input Required**: False

>	**Attribute Type**: Dictionary

>	**Description**: One property per line as 'name: value' (same typing rules as Instance Properties).

>	| Parameter Name | Parameter Value |
>	|---|---|
>	| example_key | example_value |


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
