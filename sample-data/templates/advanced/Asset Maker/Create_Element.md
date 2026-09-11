___

## Create Element
> Create a new metadata element by instantiating an Open Metadata catalog template (the generic, low-level mechanism behind every other Asset Maker command). Advanced use only -- prefer one of the specific 'Create <Type> Element' commands when the element type has one.

### Element Type Name
>	**Input Required**: True

>	**Attribute Type**: Simple

>	**Description**: The Open Metadata type name of the element to create (e.g. 'CSVFile').


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


### Initial Status
>	**Input Required**: False

>	**Attribute Type**: Valid Value

>	**Description**: The initial InstanceStatus of the new element.

>	**Valid Values**: ACTIVE,DRAFT,PREPARED,PROPOSED,APPROVED,REJECTED,DEPRECATED,OTHER

>	**Default Value**: ACTIVE


### Generic Initial Classifications
>	**Input Required**: False

>	**Attribute Type**: Dictionary

>	**Description**: Map of classification name to classification properties to apply to the new element on creation.

>	| Parameter Name | Parameter Value |
>	|---|---|
>	| example_key | example_value |


### Anchor ID
>	**Input Required**: False

>	**Attribute Type**: Reference Name

>	**Description**: Name of the anchoring element.


### Is Own Anchor
>	**Input Required**: False

>	**Attribute Type**: Bool

>	**Description**: A flag indicating if the element is its own anchor or is anchored to a different element.

>	**Alternative Labels**: Own Anchor

>	**Default Value**: true


### Anchor Scope IDs
>	**Input Required**: False

>	**Attribute Type**: Reference Name List

>	**Description**: A list of IDs that are anchor scopes for this element.


### Effective From
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: The beginning of when an element is viewable.


### Effective To
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: The ending time at which an element is visible.


### Effective Time
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: The time at which an element must be effective in order to be returned by the request.


### Parent ID
>	**Input Required**: False

>	**Attribute Type**: Reference Name

>	**Description**: Name of the parent

>	**Alternative Labels**: Parent;


### Parent Relationship Type Name
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: The type of parent relationship.


### Parent Relationship Attributes
>	**Input Required**: False

>	**Attribute Type**: Dictionary

>	**Description**: A dictionary of relationship attributes to establish the parent relationship.

>	| Parameter Name | Parameter Value |
>	|---|---|
>	| example_key | example_value |


### Parent at End1
>	**Input Required**: False

>	**Attribute Type**: Bool

>	**Description**: A flag indicating if the parent is at end1 of the relationship

>	**Default Value**: true


### Status
>	**Input Required**: False

>	**Attribute Type**: Valid Value

>	**Description**: The status of the digital product. There is a list of valid values that this conforms to.

>	**Default Value**: ACTIVE


### User Defined Status
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: Only valid if  Status is set to OTHER. User defined & managed status values.


### Classifications
>	**Input Required**: false

>	**Attribute Type**: Named DICT

>	**Description**: Optionally specify the initial classifications for a collection. Multiple classifications can be specified. 

>	**Alternative Labels**: classification

>	| Parameter Name | Parameter Value |
>	|---|---|
>	| example_key | example_value |


### Anchor Scope Name
>	**Input Required**: False

>	**Attribute Type**: Reference Name

>	**Description**: Optional qualified name of an anchor scope.


### Merge Update
>	**Input Required**: False

>	**Attribute Type**: Bool

>	**Description**: If True, only those attributes specified in the update will be updated; If False, any attributes not provided during the update will be set to None.

>	**Alternative Labels**: Merge

>	**Default Value**: True


### Additional Properties
>	**Input Required**: False

>	**Attribute Type**: Dictionary

>	**Description**: Additional user defined values organized as name value pairs in a dictionary.

>	| Parameter Name | Parameter Value |
>	|---|---|
>	| example_key | example_value |


### External Source GUID
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: Identifier of an external source that is associated with this element.


### External Source Name
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: Name of an external element that is associated with this element.


### Supplementary Properties
>	**Input Required**: False

>	**Attribute Type**: Named DICT

>	**Description**: Provide supplementary information to the element using the structure of a glossary term

>	| Parameter Name | Parameter Value |
>	|---|---|
>	| example_key | example_value |


___
