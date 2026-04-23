___

# Create Related Media
> Create or update Related Media - an external reference to media such as images, audio, video or documents.
>
>	**Alternative Names**: Media

## Display Name
>	**Input Required**: True

>	**Attribute Type**: Simple

>	**Description**: The common name of an element.

>	**Alternative Labels**: "Term Name"


## Attribution
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: Attribution string to describe the external reference.


## Copyright
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: The copyright associated with the external reference.


## License
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: The license associated with the external reference.


## Organization
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: Organization owning the external reference.


## Reference Abstract
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: Abstract for the remote reference.

>	**Alternative Labels**: Abstract


## Reference Title
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: Title of the external reference.

>	**Alternative Labels**: Title


## Sources
>	**Input Required**: False

>	**Attribute Type**: Dictionary

>	**Description**: A map of source strings (e.g. URL, DOI, ISBN).

>	**Alternative Labels**: Reference Sources

>	| Parameter Name | Parameter Value |
>	|---|---|
>	| example_key | example_value |


## Default Media Usage
>	**Input Required**: False

>	**Attribute Type**: Valid Value

>	**Description**: How the media is being used by default.

>	**Valid Values**: ICON,THUMBNAIL,ILLUSTRATION,USAGE_GUIDANCE,OTHER


## Default Media Usage Other Id
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: An id associated with the default media usage when not using a standard valid value.


## Media Type
>	**Input Required**: False

>	**Attribute Type**: Valid Value

>	**Description**: Type of media (e.g. image, audio, video, document).

>	**Valid Values**: IMAGE,AUDIO,DOCUMENT,VIDEO,OTHER


## Media Type Other Id
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: An id associated with the media type when not using a standard valid value.


## Journal Entry
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: A text entry into a journal.


## Category
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: A user-defined category for the element, used to group related elements for display or search purposes.

>	**Alternative Labels**: Category Name


## Description
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: A description.


## Qualified Name
>	**Input Required**: False

>	**Attribute Type**: QN

>	**Description**: The unique, text name of an element.


## Content Status
>	**Input Required**: False

>	**Attribute Type**: Valid Value

>	**Description**: The lifecycle status of an element.

>	**Valid Values**: DRAFT,PREPARED,PROPOSED,APPROVED,REJECTED,ACTIVE,DEPRECATED,OTHER

>	**Default Value**: ACTIVE


## Search Keywords
>	**Input Required**: False

>	**Attribute Type**: Simple List

>	**Description**: A list of search keywords.


## GUID
>	**Input Required**: False

>	**Attribute Type**: GUID

>	**Description**: A unique identifier - typically of an element in this context.

>	**Alternative Labels**: guid; Guid


## URL
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: URL for further information.


## Version Identifier
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: The version of the element

>	**Alternative Labels**: Version

>	**Default Value**: 1.0


## Authors
>	**Input Required**: False

>	**Attribute Type**: Simple List

>	**Description**: The authors.


___
