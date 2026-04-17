# Report
> Runs a named pyegeria report spec (FormatSet) via hey_egeria run_report. Returns formatted output from the Egeria repository — not an element creation command.

## Report Spec
>	**Input Required**: True

>	**Attribute Type**: Simple

>	**Description**: The name of the report spec (FormatSet) to run, e.g. 'Digital-Products', 'Collections', 'My-User-MD'. This is the primary identifier for the report — equivalent to --report in the CLI.

>	**Default Value**: Referenceable


## Search String
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: An optional search string to filter results by.

>	**Default Value**: *


## Output Format
>	**Input Required**: False

>	**Attribute Type**: Valid Value

>	**Description**: Optional specification of output format for the query.

>	**Valid Values**: LIST,FORM,REPORT,MERMAID,DICT,MD,TABLE,JSON

>	**Default Value**: JSON


## Starts With
>	**Input Required**: False

>	**Attribute Type**: Bool

>	**Description**: If true, look for matches with the search string starting from the beginning of  a field.

>	**Default Value**: True


## Ends With
>	**Input Required**: False

>	**Attribute Type**: Bool

>	**Description**: If true, look for matches with the search string starting from the end of  a field.

>	**Default Value**: False


## Ignore Case
>	**Input Required**: False

>	**Attribute Type**: Bool

>	**Description**: If true, ignore the difference between upper and lower characters when matching the search string.

>	**Default Value**: False


## Metadata Element Type Name
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: Optionally filter results by the type of metadata element.


## Metadata Element Subtype Names
>	**Input Required**: False

>	**Attribute Type**: Simple List

>	**Description**: Filter results by the list of metadata elements. If none are provided, then no status filtering will be performed.


## Page Size
>	**Input Required**: False

>	**Attribute Type**: Simple Int

>	**Description**: The number of elements returned per page.

>	**Default Value**: 0


## Start From
>	**Input Required**: False

>	**Attribute Type**: Simple Int

>	**Description**: When paging through results, the starting point of the results to return.

>	**Default Value**: 0

