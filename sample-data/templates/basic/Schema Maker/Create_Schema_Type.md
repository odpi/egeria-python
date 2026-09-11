___

## Create Schema Type
> Create a new schema type element (a reusable description of a schema, independent of any element that uses it).

### Display Name
>	**Input Required**: True

>	**Attribute Type**: Simple

>	**Description**: The common name of an element.

>	**Alternative Labels**: "Term Name"


### Usage
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: The usage guidance for this element — how it is intended to be used in context.


### Is Deprecated
>	**Input Required**: False

>	**Attribute Type**: Bool

>	**Description**: If true, this element has been deprecated and should not be used in new designs.

>	**Default Value**: false


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


### Author
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: Author of this schema type.


### Encoding Standard
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: Encoding standard used for this schema type (e.g. 'UTF-8', 'ASN.1').


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
