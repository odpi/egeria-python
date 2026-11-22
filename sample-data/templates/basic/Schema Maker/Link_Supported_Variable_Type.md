___

## Link Supported Variable Type
> Record a schema type describing a variable that an element (such as a process) supports (the SupportedVariableType relationship), with Position (0 means unset) and Min/Max Cardinality. Needs Egeria 6.4.

### Label
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: A label used to identify or categorise a relationship link.

>	**Alternative Labels**: Wire Label


### Element
>	**Input Required**: False

>	**Attribute Type**: Reference Name

>	**Description**: The element at the other end of the relationship (any Referenceable): its qualified name, display name or GUID. For an assessment, the element that was assessed.

>	**Alternative Labels**: Assessed Element


### Position
>	**Input Required**: False

>	**Attribute Type**: Simple Int

>	**Description**: The ordinal position: of a data field within its containing data structure, or of a data value among an element's processing variables or a parent value's embedded values (0 means unset).

>	**Default Value**: 0


### Journal Entry
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: A text entry into a journal.


### Description
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: A description.


### Schema Type
>	**Input Required**: False

>	**Attribute Type**: Reference Name

>	**Description**: A schema type (e.g. a TabularSchemaType): for a data structure, the physical schema type equivalent to it (SchemaTypeDefinition relationship); for a process, the type of a variable it supports (SupportedVariableType relationship).


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


___
