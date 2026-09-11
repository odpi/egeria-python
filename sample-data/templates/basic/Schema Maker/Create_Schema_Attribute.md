___

## Create Schema Attribute
> Create a new schema attribute element (one member/column/field of a schema type).

### Display Name
>	**Input Required**: True

>	**Attribute Type**: Simple

>	**Description**: The common name of an element.

>	**Alternative Labels**: "Term Name"


### Usage
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: The usage guidance for this element — how it is intended to be used in context.


### Qualified Name
>	**Input Required**: False

>	**Attribute Type**: QN

>	**Description**: The unique, text name of an element.


### Description
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: A description.


### Category
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: A user-defined category for the element, used to group related elements for display or search purposes.

>	**Alternative Labels**: Category Name


### Content Status
>	**Input Required**: False

>	**Attribute Type**: Valid Value

>	**Description**: The lifecycle status of an element.

>	**Valid Values**: DRAFT,PREPARED,PROPOSED,APPROVED,REJECTED,ACTIVE,DEPRECATED,OTHER

>	**Default Value**: ACTIVE


### Journal Entry
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: 


### Version Identifier
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: The version of the element

>	**Alternative Labels**: Version

>	**Default Value**: 1.0


### URL
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: URL for further information.


### Authors
>	**Input Required**: False

>	**Attribute Type**: Simple List

>	**Description**: The authors.


### Initial Classifications
>	**Input Required**: False

>	**Attribute Type**: Dictionary

>	**Description**: Map of classification name to classification properties to apply on creation.

>	| Parameter Name | Parameter Value |
>	|---|---|
>	| example_key | example_value |


### Element Position
>	**Input Required**: False

>	**Attribute Type**: Simple Int

>	**Description**: Position of this attribute within its parent schema (0-based).


### Min Cardinality
>	**Input Required**: False

>	**Attribute Type**: Simple Int

>	**Description**: Minimum number of values allowed for this attribute (-1 means unbounded/unknown).

>	**Default Value**: -1


### Max Cardinality
>	**Input Required**: False

>	**Attribute Type**: Simple Int

>	**Description**: Maximum number of values allowed for this attribute (-1 means unbounded).

>	**Default Value**: -1


### Allows Duplicate Values
>	**Input Required**: False

>	**Attribute Type**: Bool

>	**Description**: True if duplicate values are allowed for this attribute.

>	**Default Value**: true


### Is Ordered Values
>	**Input Required**: False

>	**Attribute Type**: Bool

>	**Description**: True if the values of this attribute are ordered.

>	**Default Value**: false


### Default Value Override
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: Override for the default value defined by this attribute's schema type.


### Identifier
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: role identifier

>	**Alternative Labels**: ID


### GUID
>	**Input Required**: False

>	**Attribute Type**: GUID

>	**Description**: A system generated unique identifier.

>	**Alternative Labels**: Guid; guid


### Search Keywords
>	**Input Required**: False

>	**Attribute Type**: Simple List

>	**Description**: Keywords to facilitate finding the element


___
