___

## Update License
> Update the properties of an existing License relationship, identified by its own relationship GUID (License GUID, as returned by Link License).

### Label
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: A label used to identify or categorise a relationship link.

>	**Alternative Labels**: Wire Label


### License GUID
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: Unique identifier of the license.


### Licensed By
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: The name of the person or organization that granted the license.


### Licensed By Property Name
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: The property name used to identify the licensor element (used with Licensed By Type Name).


### Licensed By Type Name
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: The open metadata type name of the element that granted the license (used with Licensed By Property Name).


### Conditions
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: Conditions for certifications or licenses.


### Custodian
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: Custodian of the license or certification.


### Custodian Property Name
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: The property name used to identify the custodian element (used with Custodian Type Name).


### Custodian Type Name
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: The open metadata type name of the element acting as custodian (used with Custodian Property Name to identify the custodian).


### End Date
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: Date at which the license or certification expires.


### Licensee
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: The licensee.


### Licensee Property Name
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: The property name used to identify the licensee element (used with Licensee Type Name).


### Licensee Type Name
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: The open metadata type name of the element receiving the license (used with Licensee Property Name).


### Obligations
>	**Input Required**: False

>	**Attribute Type**: Dictionary

>	**Description**: A dictionary of property:value pairs describing obligations.

>	| Parameter Name | Parameter Value |
>	|---|---|
>	| example_key | example_value |


### Start Date
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: Date at which the license or certification takes effect.


### Journal Entry
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: A text entry into a journal.


### Description
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: A description.


### Entitlements
>	**Input Required**: False

>	**Attribute Type**: Dictionary

>	**Description**: A dictionary of property:value pairs describing entitlements.

>	| Parameter Name | Parameter Value |
>	|---|---|
>	| example_key | example_value |


### Restrictions
>	**Input Required**: False

>	**Attribute Type**: Dictionary

>	**Description**: A dictionary of property:value pairs describing restrictions.

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


### Effective From
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: The beginning of when an element is viewable.


### Effective Time
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: The time at which an element must be effective in order to be returned by the request.


### Effective To
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: The ending time at which an element is visible.


### External Source GUID
>	**Input Required**: False

>	**Attribute Type**: GUID

>	**Description**: The unique identifier of an external source.


### External Source Name
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: The name of an external source


### For Duplicate Processing
>	**Input Required**: False

>	**Attribute Type**: Bool

>	**Description**: Flag indicating if the request is to support duplicate processing.


### For Lineage
>	**Input Required**: False

>	**Attribute Type**: Bool

>	**Description**: Flag indicating if the request is to support lineage.


### Request ID
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: A user provided or system generated request id for a conversation.


### Anchor Scope IDs
>	**Input Required**: False

>	**Attribute Type**: Reference Name List

>	**Description**: A list of IDs that are anchor scopes for this element.


### Make Anchor
>	**Input Required**: False

>	**Attribute Type**: Bool

>	**Description**: Is the element at end2 an anchor to end1?

>	**Default Value**: false


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


### Supplementary Properties
>	**Input Required**: False

>	**Attribute Type**: Named DICT

>	**Description**: Provide supplementary information to the element using the structure of a glossary term

>	| Parameter Name | Parameter Value |
>	|---|---|
>	| example_key | example_value |


___
