___

## Detach Search Keyword
> Remove a search keyword (0012 SearchKeyword), identified by the keyword entitys own GUID. Deletes the keyword entity itself, not just its link to an element.

### Label
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: A label used to identify or categorise a relationship link.

>	**Alternative Labels**: Wire Label


### Search Keyword GUID
>	**Input Required**: False

>	**Attribute Type**: Reference Name

>	**Description**: The unique identifier of the SearchKeyword entity itself (0012), as opposed to the element it is attached to. Required for Update/Detach; not used for Attach (which creates a new keyword).


### Journal Entry
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: A text entry into a journal.


### Description
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: A description.


___
