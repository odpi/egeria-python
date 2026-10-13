___

## Detach Element from Valid Values
> Remove the generic ValidValuesAssignment relationship between an element and its ValidValueSet.

### Element Id
>	**Input Required**: True

>	**Attribute Type**: Reference Name

>	**Description**: The unique identifier (qualified name or GUID) of the element being referenced.

>	**Alternative Labels**: Element Name; Member Id


### Valid Value Set
>	**Input Required**: True

>	**Attribute Type**: Reference Name

>	**Description**: The valid value set/definition that defines the allowed values for this element (ValidValuesAssignment relationship).

>	**Alternative Labels**: Valid Value Definition


### Journal Entry
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: A text entry into a journal.


### Strict Requirement
>	**Input Required**: False

>	**Attribute Type**: Bool

>	**Description**: If true, the element must use one of the set's values; if false, the values are suggestions (strictRequirement on ValidValuesAssignment).

>	**Default Value**: true


___
