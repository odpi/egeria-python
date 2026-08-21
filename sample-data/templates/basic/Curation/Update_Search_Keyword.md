___

## Update Search Keyword
> Update a search keyword already attached to an element (0012 SearchKeyword), identified by the keyword entitys own GUID.

### Keyword
>	**Input Required**: True

>	**Attribute Type**: Simple

>	**Description**: Text of the search keyword being attached to the element (0012 SearchKeyword).


### Label
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: A label used to identify or categorise a relationship link.

>	**Alternative Labels**: Wire Label


### Search Keyword GUID
>	**Input Required**: False

>	**Attribute Type**: Reference Name

>	**Description**: The unique identifier of the SearchKeyword entity itself (0012), as opposed to the element it is attached to. Required for Update/Detach; not used for Attach (which creates a new keyword).


### Keyword Description
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: Description of the search keyword (0012 SearchKeyword).


### Journal Entry
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: A text entry into a journal.


### Description
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: A description.


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


___
