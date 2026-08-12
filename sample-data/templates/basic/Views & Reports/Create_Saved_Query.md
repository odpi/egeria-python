___

## Create Saved Query
> Defines a saved query -- a RESTful query to Egeria that returns Open Metadata Elements -- that can be connected to a Results Set via the SmartQuery relationship (Egeria PR #9200, 0725 Smart Collections).

### Display Name
>	**Input Required**: True

>	**Attribute Type**: Simple

>	**Description**: The common name of an element.

>	**Alternative Labels**: "Term Name"


### Deployed Implementation Type
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: The implementation type for a deploymed resource.

>	**Alternative Labels**: Deployed Impl Type


### Namespace Path
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: The namespace path that qualifies the element's name within a larger naming hierarchy.


### Resource Name
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: Name of a resource.


### Journal Entry
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: A text entry into a journal.


### Category
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: A user-defined category for the element, used to group related elements for display or search purposes.

>	**Alternative Labels**: Category Name


### Description
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: A description.


### Legal
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: Copyright and/or license information for the element or associated resource.


### Qualified Name
>	**Input Required**: False

>	**Attribute Type**: QN

>	**Description**: The unique, text name of an element.


### Search Keywords
>	**Input Required**: False

>	**Attribute Type**: Simple List

>	**Description**: A list of search keywords.


### GUID
>	**Input Required**: False

>	**Attribute Type**: GUID

>	**Description**: A unique identifier - typically of an element in this context.

>	**Alternative Labels**: guid; Guid


### URL
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: URL for further information.


### Version Identifier
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: The version of the element

>	**Alternative Labels**: Version

>	**Default Value**: 1.0


### Query URL
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: The REST URL used to issue the saved query.


### Query Request Body
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: The REST request body (typically JSON) used to issue the saved query.


___
