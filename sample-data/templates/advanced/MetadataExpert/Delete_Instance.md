___

## Delete Instance
> Delete a metadata element (instance). Defaults to SOFT_DELETE. PURGE is permanent and only works on an element already soft deleted; it also requires Confirm Delete GUID to repeat the GUID.

### Metadata Element GUID
>	**Input Required**: True

>	**Attribute Type**: GUID

>	**Description**: GUID of the metadata element.


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


___
