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


### Confidence
>	**Input Required**: False

>	**Attribute Type**: Simple Int

>	**Description**: A percent confidence in the proposed adding of the member.


### Source
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: The source of the information.


### Steward
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: The identifier of the steward responsible for the element.


### Steward Property Name
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: Property name used to identify the type of the steward.


### Steward Type Name
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: The type name of the steward element.


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
