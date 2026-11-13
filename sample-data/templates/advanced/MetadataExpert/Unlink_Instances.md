___

## Unlink Instances
> Delete a relationship between two metadata elements. Defaults to SOFT_DELETE. PURGE is permanent and only works on a relationship already soft deleted; it also requires Confirm Delete GUID to repeat the Relationship GUID.

### Relationship GUID
>	**Input Required**: True

>	**Attribute Type**: GUID

>	**Description**: GUID of the relationship.


### Delete Method
>	**Input Required**: False

>	**Attribute Type**: Valid Value

>	**Description**: How to delete.

>	**Valid Values**: SOFT_DELETE,PURGE,ARCHIVE,LOOK_FOR_LINEAGE

>	**Default Value**: SOFT_DELETE


### Confirm Delete GUID
>	**Input Required**: False

>	**Attribute Type**: GUID

>	**Description**: Required when Delete Method is PURGE or HARD_DELETE: repeat the GUID being deleted. A purge cannot be undone and must have been soft deleted first.


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


___
