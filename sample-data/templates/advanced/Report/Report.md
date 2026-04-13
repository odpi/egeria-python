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


## Limit Result by Status
>	**Input Required**: False

>	**Attribute Type**: Valid Value

>	**Description**: One of the status values from a list of valid values.

>	**Valid Values**: UNKNOWN,DRAFT,PREPARED,PROPOSED,APPROVED,REJECTED,APPROVED_CONCEPT,UNDER_DEVELOPMENT,DEVELOPMENT_COMPLETE,APPROVED_FOR_DEPLOYMENT,STANDBY,ACTIVE,FAILED,DISABLED,COMPLETE,DEPRECATED,OTHER,DELETED

>	**Default Value**: ['ACTIVE']


## Skip Relationships
>	**Input Required**: False

>	**Attribute Type**: Simple List

>	**Description**: Allow listed relationships to be skipped in the output returned.


## Include Only Relationships
>	**Input Required**: False

>	**Attribute Type**: Simple List

>	**Description**: Include information only about specified relationships.


## Skip Classified Elements
>	**Input Required**: False

>	**Attribute Type**: Simple List

>	**Description**: Skip elements with the any of the specified classifications.


## Include Only Classified Elements
>	**Input Required**: False

>	**Attribute Type**: Simple List

>	**Description**: Include only elements with the specified classifications.


## Governance Zone Filter
>	**Input Required**: False

>	**Attribute Type**: Simple List

>	**Description**: Include only elements in one of the specified governance zones.


## Graph Query Depth
>	**Input Required**: False

>	**Attribute Type**: Simple Int

>	**Description**: The depth of the hierarchy to return. Default is 5. Specifying 0 returns only the top level attributes.

>	**Default Value**: 1


## Effective Time
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: The time at which an element must be effective in order to be returned by the request.


## AsOfTime
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: An ISO-8601 string representing the time to view the state of the repository.


## Output Sort Order
>	**Input Required**: False

>	**Attribute Type**: Valid Value

>	**Description**: How to order the results. The sort order can be selected from a list of valid value.

>	**Valid Values**: ANY,CREATION_DATE_RECENT,CREATION_DATA_OLDEST,LAST_UPDATE_RECENT,LAST_UPDATE_OLDEST,PROPERTY_ASCENDING,PROPERTY_DESCENDING


## Order Property Name
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: The property to use for sorting if the sort_order_property is PROPERTY_ASCENDING or PROPERTY_DESCENDING


## Anchor Scope ID
>	**Input Required**: False

>	**Attribute Type**: Reference Name

>	**Description**: Anchor scope to restrict search.

>	**Alternative Labels**: Anchor Scope

