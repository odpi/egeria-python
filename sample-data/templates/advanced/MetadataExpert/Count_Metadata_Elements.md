___

## Count Metadata Elements
> Return the number of metadata elements matching the criteria, without retrieving them.

### Count Element Type Name
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: Only count elements of this metadata element type (and subtypes).


### Count Search String
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: Only count elements matching this search string.


### Count Push Down
>	**Input Required**: False

>	**Attribute Type**: Bool

>	**Description**: True: the repository counts rows itself (fast, skips per-element visibility checks). False: the server retrieves and counts matching elements. Omit for the server default.


___
