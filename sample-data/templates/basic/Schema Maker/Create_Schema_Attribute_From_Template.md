___

## Create Schema Attribute From Template
> Create a new schema attribute element by instantiating an Open Metadata catalog template.

### Template GUID
>	**Input Required**: True

>	**Attribute Type**: Reference Name

>	**Description**: GUID of the catalog template to instantiate.


### Placeholder Property Values
>	**Input Required**: True

>	**Attribute Type**: Dictionary

>	**Description**: Map of placeholder name to value, substituted into the template.

>	| Parameter Name | Parameter Value |
>	|---|---|
>	| example_key | example_value |


### Category
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: A user specified category name that can be used for example, to define product types or agreement types.

>	**Alternative Labels**: Category Name


### Qualified Name
>	**Input Required**: False

>	**Attribute Type**: QN

>	**Description**: A unique qualified name for the element. Generated using the qualified name pattern  if not user specified.


### Journal Entry
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: 


### Template Properties
>	**Input Required**: False

>	**Attribute Type**: Dictionary

>	**Description**: Overrides for specific properties defined by the template.

>	| Parameter Name | Parameter Value |
>	|---|---|
>	| example_key | example_value |


### Version Identifier
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: Published product version identifier.

>	**Alternative Labels**: Version

>	**Default Value**: 1.0


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


### URL
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: Link to supporting information


### Search Keywords
>	**Input Required**: False

>	**Attribute Type**: Simple List

>	**Description**: Keywords to facilitate finding the element


___
