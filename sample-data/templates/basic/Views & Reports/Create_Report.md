___

## Create Report
> Defines a report with optional default parameters set, that can be placed on a Dashboard.

### Display Name
>	**Input Required**: True

>	**Attribute Type**: Simple

>	**Description**: The common name of an element.

>	**Alternative Labels**: "Term Name"


### Report Spec
>	**Input Required**: True

>	**Attribute Type**: Simple

>	**Description**: The name of the report spec (FormatSet) to run, e.g. 'Digital-Products', 'Collections', 'My-User-MD'. This is the primary identifier for the report — equivalent to --report in the CLI.

>	**Default Value**: Referenceable


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


### Analytic Parameters
>	**Input Required**: False

>	**Attribute Type**: Dictionary

>	**Description**: Name-Value pairs of analytic parameters

>	| Parameter Name | Parameter Value |
>	|---|---|
>	| example_key | example_value |


### Ends With
>	**Input Required**: False

>	**Attribute Type**: Bool

>	**Description**: If true, look for matches with the search string starting from the end of  a field.

>	**Default Value**: False


### Ignore Case
>	**Input Required**: False

>	**Attribute Type**: Bool

>	**Description**: If true, ignore the difference between upper and lower characters when matching the search string.

>	**Default Value**: False


### Metadata Element Subtype Names
>	**Input Required**: False

>	**Attribute Type**: Simple List

>	**Description**: Filter results by the list of metadata elements. If none are provided, then no status filtering will be performed.


### Metadata Element Type Name
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: Optionally filter results by the type of metadata element.


### Output Format
>	**Input Required**: False

>	**Attribute Type**: Valid Value

>	**Description**: Optional specification of output format for the query.

>	**Valid Values**: LIST,FORM,REPORT,MERMAID,DICT,MD,TABLE,JSON

>	**Default Value**: JSON


### Page Size
>	**Input Required**: False

>	**Attribute Type**: Simple Int

>	**Description**: The number of elements returned per page.

>	**Default Value**: 0


### Search String
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: An optional search string to filter results by.

>	**Default Value**: *


### Start From
>	**Input Required**: False

>	**Attribute Type**: Simple Int

>	**Description**: When paging through results, the starting point of the results to return.

>	**Default Value**: 0


### Starts With
>	**Input Required**: False

>	**Attribute Type**: Bool

>	**Description**: If true, look for matches with the search string starting from the beginning of  a field.

>	**Default Value**: True


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


### Report Parameters
>	**Input Required**: False

>	**Attribute Type**: Dictionary

>	**Description**: Name-Value pairs of extra parameters for the target Report Spec's action that aren't part of the standard find/search attribute set (e.g. collection_guid for the "Collection Members" report). Keys must match exactly what the target report spec's action expects.

>	| Parameter Name | Parameter Value |
>	|---|---|
>	| example_key | example_value |


___
