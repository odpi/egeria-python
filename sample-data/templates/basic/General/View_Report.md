# View Report
> This can be used to produce a report using any output format set.
>
>	**Alternative Names**: View MD; View FORM; View DICT; View LIST; View HTML

# Required

## Report Spec
>	**Input Required**: True

>	**Description**: Optional specification of an report  that defines the attributes/columns that will be returned.

>	**Alternative Labels**: Output Format Set; Report

>	**Default Value**: Referenceable


# Common Properties

## Category
>	**Input Required**: False

>	**Description**: A user specified category name that can be used for example, to define product types or agreement types.

>	**Alternative Labels**: Category Name


## Qualified Name
>	**Input Required**: False

>	**Description**: A unique qualified name for the element. Generated using the qualified name pattern  if not user specified.


## Journal Entry
>	**Input Required**: False

>	**Description**: 


# Additional Properties

## Search String
>	**Input Required**: False

>	**Description**: An optional search string to filter results by.

>	**Alternative Labels**: Filter_String

>	**Default Value**: *


## Output Format
>	**Input Required**: False

>	**Description**: Optional specification of output format for the query.

>	**Alternative Labels**: Format

>	**Valid Values**: LIST; FORM; REPORT; MERMAID; DICT

>	**Default Value**: LIST


## Starts With
>	**Input Required**: False

>	**Description**: If true, look for matches with the search string starting from the beginning of  a field.

>	**Default Value**: True


## Ends With
>	**Input Required**: False

>	**Description**: If true, look for matches with the search string starting from the end of  a field.

>	**Default Value**: False


## Ignore Case
>	**Input Required**: False

>	**Description**: If true, ignore the difference between upper and lower characters when matching the search string.

>	**Default Value**: False


## Metadata Element Subtype Names
>	**Input Required**: False

>	**Description**: Filter results by the list of metadata elements. If none are provided, then no status filtering will be performed.


## Metadata Element Type Name
>	**Input Required**: False

>	**Description**: Optionally filter results by the type of metadata element.


## Skip Classified Elements
>	**Input Required**: False

>	**Description**: Skip elements with the any of the specified classifications.


## Include Only Classified Elements
>	**Input Required**: False

>	**Description**: Include only elements with the specified classifications.


## AsOfTime
>	**Input Required**: False

>	**Description**: An ISO-8601 string representing the time to view the state of the repository.

>	**Alternative Labels**: As Of Time


## Sort Order
>	**Input Required**: False

>	**Description**: How to order the results. The sort order can be selected from a list of valid value.

>	**Valid Values**: ANY; CREATION_DATE_RECENT; CREATION_DATA_OLDEST; LAST_UPDATE_RECENT; LAST_UPDATE_OLDEST; PROPERTY_ASCENDING; PROPERTY_DESCENDING


## Order Property Name
>	**Input Required**: False

>	**Description**: The property to use for sorting if the sort_order_property is PROPERTY_ASCENDING or PROPERTY_DESCENDING


## Page Size
>	**Input Required**: False

>	**Description**: The number of elements returned per page.

>	**Default Value**: 0


## Start From
>	**Input Required**: False

>	**Description**: When paging through results, the starting point of the results to return.

>	**Default Value**: 0


## Version Identifier
>	**Input Required**: False

>	**Description**: Published product version identifier.

>	**Default Value**: 1.0


## Identifier
>	**Input Required**: False

>	**Description**: role identifier


## GUID
>	**Input Required**: False

>	**Description**: A system generated unique identifier.

>	**Alternative Labels**: Guid; guid


## URL
>	**Input Required**: False

>	**Description**: Link to supporting information


## Search Keywords
>	**Input Required**: False

>	**Description**: Keywords to facilitate finding the element

