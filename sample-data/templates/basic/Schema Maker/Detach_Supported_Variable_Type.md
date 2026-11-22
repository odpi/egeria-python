___

## Detach Supported Variable Type
> Remove the SupportedVariableType relationship between an element and a schema type. Needs Egeria 6.4.

### Element
>	**Input Required**: False

>	**Attribute Type**: Reference Name

>	**Description**: The element at the other end of the relationship (any Referenceable): its qualified name, display name or GUID. For an assessment, the element that was assessed.

>	**Alternative Labels**: Assessed Element


### Journal Entry
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: A text entry into a journal.


### Schema Type
>	**Input Required**: False

>	**Attribute Type**: Reference Name

>	**Description**: A schema type (e.g. a TabularSchemaType): for a data structure, the physical schema type equivalent to it (SchemaTypeDefinition relationship); for a process, the type of a variable it supports (SupportedVariableType relationship).


___
