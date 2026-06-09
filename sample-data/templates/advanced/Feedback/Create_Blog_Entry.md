___

## Create Blog Entry
> Add a blog entry.

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


### Is Own Anchor
>	**Input Required**: False

>	**Attribute Type**: Bool

>	**Description**: Generally True. 

>	**Alternative Labels**: Own Anchor

>	**Default Value**: True


### Anchor ID
>	**Input Required**: False

>	**Attribute Type**: Reference Name

>	**Description**: Anchor identity for the collection. Typically a qualified name but if display name is unique then it could be used (not recommended)


### Parent ID
>	**Input Required**: False

>	**Attribute Type**: Reference Name

>	**Description**: Unique name of the parent element.

>	**Alternative Labels**: Parent;


### Parent Relationship Type Name
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: The kind of the relationship to the parent element.


### Anchor Scope Name
>	**Input Required**: False

>	**Attribute Type**: Reference Name

>	**Description**: Optional qualified name of an anchor scope.


### Parent at End1
>	**Input Required**: False

>	**Attribute Type**: Bool

>	**Description**: Is the parent at end1 of the relationship?

>	**Default Value**: True


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
