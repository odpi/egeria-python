___

## Assign Data Value Specification
> Link a data value specification, DataClass, DataGrain,  to a referenceable element providing a definition.
>
>	**Alternative Names**: Link Data Value Specification; Attach Data Value Specification to Element

### Data Value Specification
>	**Input Required**: True

>	**Attribute Type**: Reference Name

>	**Description**: The data value specification to use in a relationship. Preferable to use a qualified name.


### Element Id
>	**Input Required**: True

>	**Attribute Type**: Reference Name

>	**Description**: The unique identifier (qualified name or GUID) of the element being referenced.

>	**Alternative Labels**: Element Name; Member Id


### Assignment Status
>	**Input Required**: False

>	**Attribute Type**: Valid Value

>	**Description**: Status of a value assignment.

>	**Valid Values**: DISCOVERED,PROPOSED,IMPORTED,VALIDATED,DEPRECATED,OBSOLETE,OTHER

>	**Default Value**: DISCOVERED


### Method
>	**Input Required**: False

>	**Attribute Type**: Simple List

>	**Description**: A method for value assignment.


### Threshold
>	**Input Required**: False

>	**Attribute Type**: Simple Int

>	**Description**: Threshold  for assignment.


___
