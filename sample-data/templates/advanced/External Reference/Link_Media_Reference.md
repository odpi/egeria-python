___

## Link Media Reference
> Link a related media reference to a referenceable via the MediaReferenceLink relationship.
>
>	**Alternative Names**: Referenceable->Media Reference; Media Reference

### Element Name
>	**Input Required**: True

>	**Attribute Type**: Reference Name

>	**Description**: A referenceable to link to the external reference.

>	**Alternative Labels**: Referenceable


### Media Reference
>	**Input Required**: True

>	**Attribute Type**: Reference Name

>	**Description**: The related media reference to link to.


### Media Id
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: An identifier of the media being referenced.


### Media Usage
>	**Input Required**: False

>	**Attribute Type**: Valid Value

>	**Description**: How the media is being used in this specific link.

>	**Valid Values**: ICON,THUMBNAIL,ILLUSTRATION,USAGE_GUIDANCE,OTHER


### Media Usage Other Id
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: An id associated with the media usage when not using a standard valid value.


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
