# Add Member to Collection
> Add/Remove a member to/from a collection.
>
>	**Alternative Names**: Member; Member to Collection; Member to Folder; Member->Collection; Member from Collection; Member from Folder

## Element Id
>	**Input Required**: True

>	**Attribute Type**: Reference Name

>	**Description**: The unique identifier (qualified name or GUID) of the element being referenced.

>	**Alternative Labels**: Element Name; Member Id


## Label
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: A label used to identify or categorise a relationship link.

>	**Alternative Labels**: Wire Label


## Membership Rationale
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: Rationale for membership.


## Membership Status
>	**Input Required**: False

>	**Attribute Type**: Valid Value

>	**Description**: The status of adding a member to a collection.

>	**Valid Values**: UNKNOWN,DISCOVERED,PROPOSED,IMPORTED,VALIDATED,DEPRECATED,OBSOLETE,OTHER

>	**Default Value**: PROPOSED


## Notes
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: Notes and observations about the element.


## Journal Entry
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: A text entry into a journal.


## Description
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: A description.


## Collection Id
>	**Input Required**: False

>	**Attribute Type**: Reference Name

>	**Description**: The unique identifier (qualified name or GUID) of the collection.


## Category
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: A user specified category name that can be used for example, to define product types or agreement types.

>	**Alternative Labels**: Category Name


## Qualified Name
>	**Input Required**: False

>	**Attribute Type**: QN

>	**Description**: A unique qualified name for the element. Generated using the qualified name pattern  if not user specified.


## Version Identifier
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: Published product version identifier.

>	**Alternative Labels**: Version

>	**Default Value**: 1.0


## Identifier
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: role identifier

>	**Alternative Labels**: ID


## GUID
>	**Input Required**: False

>	**Attribute Type**: GUID

>	**Description**: A system generated unique identifier.

>	**Alternative Labels**: Guid; guid


## URL
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: Link to supporting information


## Search Keywords
>	**Input Required**: False

>	**Attribute Type**: Simple List

>	**Description**: Keywords to facilitate finding the element


## Effective From
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: The beginning of when an element is viewable.


## Effective Time
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: The time at which an element must be effective in order to be returned by the request.


## Effective To
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: The ending time at which an element is visible.


## External Source GUID
>	**Input Required**: False

>	**Attribute Type**: GUID

>	**Description**: The unique identifier of an external source.


## External Source Name
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: The name of an external source


## For Duplicate Processing
>	**Input Required**: False

>	**Attribute Type**: Bool

>	**Description**: Flag indicating if the request is to support duplicate processing.


## For Lineage
>	**Input Required**: False

>	**Attribute Type**: Bool

>	**Description**: Flag indicating if the request is to support lineage.


## Request ID
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: A user provided or system generated request id for a conversation.


## Anchor Scope IDs
>	**Input Required**: False

>	**Attribute Type**: Reference Name List

>	**Description**: A list of IDs that are anchor scopes for this element.


## Make Anchor
>	**Input Required**: False

>	**Attribute Type**: Bool

>	**Description**: Is the element at end2 an anchor to end1?

>	**Default Value**: false


## Confidence
>	**Input Required**: False

>	**Attribute Type**: Simple Int

>	**Description**: A percent confidence in the proposed adding of the member.


## Expression
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: An expression describing a membership, relationship or classification.


## Source
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: The source of the information.


## Steward
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: The identifier of the steward responsible for the element.


## Steward Property Name
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: Property name used to identify the type of the steward.


## Steward Type Name
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: The type name of the steward element.


## User Defined Status
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: A user-defined status value. Only valid when the primary status is set to OTHER.


## Status
>	**Input Required**: False

>	**Attribute Type**: Valid Value

>	**Description**: The status of the digital product. There is a list of valid values that this conforms to.

>	**Default Value**: ACTIVE


## Classifications
>	**Input Required**: false

>	**Attribute Type**: Named DICT

>	**Description**: Optionally specify the initial classifications for a collection. Multiple classifications can be specified. 

>	**Alternative Labels**: classification


## Is Own Anchor
>	**Input Required**: False

>	**Attribute Type**: Bool

>	**Description**: Generally True. 

>	**Alternative Labels**: Own Anchor

>	**Default Value**: True


## Anchor ID
>	**Input Required**: False

>	**Attribute Type**: Reference Name

>	**Description**: Anchor identity for the collection. Typically a qualified name but if display name is unique then it could be used (not recommended)


## Parent ID
>	**Input Required**: False

>	**Attribute Type**: Reference Name

>	**Description**: Unique name of the parent element.

>	**Alternative Labels**: Parent;


## Parent Relationship Type Name
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: The kind of the relationship to the parent element.


## Anchor Scope Name
>	**Input Required**: False

>	**Attribute Type**: Reference Name

>	**Description**: Optional qualified name of an anchor scope.


## Parent at End1
>	**Input Required**: False

>	**Attribute Type**: Bool

>	**Description**: Is the parent at end1 of the relationship?

>	**Default Value**: True


## Merge Update
>	**Input Required**: False

>	**Attribute Type**: Bool

>	**Description**: If True, only those attributes specified in the update will be updated; If False, any attributes not provided during the update will be set to None.

>	**Alternative Labels**: Merge

>	**Default Value**: True


## Additional Properties
>	**Input Required**: False

>	**Attribute Type**: Dictionary

>	**Description**: Additional user defined values organized as name value pairs in a dictionary.


## Supplementary Properties
>	**Input Required**: False

>	**Attribute Type**: Named DICT

>	**Description**: Provide supplementary information to the element using the structure of a glossary term

