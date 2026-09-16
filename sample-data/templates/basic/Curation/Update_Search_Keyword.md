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


___
