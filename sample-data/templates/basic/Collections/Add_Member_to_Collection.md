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

