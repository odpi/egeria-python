___

## Link Schema Attribute Definition
> Link a logical Data Field to the physical Schema Attribute that implements it (e.g. a TabularColumn), or the reverse lookup. Implemented via the generic MetadataExpert relationship mechanism (typeName: SchemaAttributeDefinition) -- no bespoke Egeria REST endpoint exists for this relationship yet (PYEGERIA_ISSUES.md ISSUE-48); will be migrated to a dedicated wrapper once Egeria ships one.

### Data Field
>	**Input Required**: True

>	**Attribute Type**: Reference Name

>	**Description**: A data field  name. Preferably a qualified name.


### Schema Attribute
>	**Input Required**: True

>	**Attribute Type**: Reference Name

>	**Description**: A physical schema attribute (e.g. a TabularColumn). Preferably a qualified name.


### Label
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: A label used to identify or categorise a relationship link.

>	**Alternative Labels**: Wire Label


### Journal Entry
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: A text entry into a journal.


### Description
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: A description.


___
