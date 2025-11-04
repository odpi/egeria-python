# View Report
>	This can be used to produce a report using any output format set.

## Search String
>	**Input Required**: False

>	**Description**: An optional search string to filter results by.

>	**Alternative Labels**: Filter

>	**Default Value**: *


## Output Format
>	**Input Required**: False

>	**Description**: Optional specification of output format for the query.

>	**Alternative Labels**: Format

>	**Valid Values**: LIST; FORM; REPORT; MERMAID; DICT

>	**Default Value**: LIST


## Output Format Set
>	**Input Required**: True

>	**Description**: Optional specification of an output format set that defines the attributes/columns that will be returned.

>	**Alternative Labels**: OUTPUT SET

>	**Default Value**: Referenceable


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


## Limit Result by Status
>	**Input Required**: False

>	**Description**: One of the status values from a list of valid values.

>	**Valid Values**: 'UNKNOWN'; 'DRAFT'; 'PREPARED'; 'PROPOSED'; 'APPROVED'; 'REJECTED';   'APPROVED_CONCEPT'; 'UNDER_DEVELOPMENT'; 'DEVELOPMENT_COMPLETE';                              'APPROVED_FOR_DEPLOYMENT'; 'STANDBY'; 'ACTIVE'; 'FAILED'; 'DISABLED'; 'COMPLETE';    'DEPRECATED'; 'OTHER' ; 'DELETED

>	**Default Value**: ['ACTIVE']


## Metadata Element Subtype Names
>	**Input Required**: False

>	**Description**: Filter results by the list of metadata elements. If none are provided, then no status filtering will be performed.


## Metadata Element Type Name
>	**Input Required**: False

>	**Description**: Optionally filter results by the type of metadata element.


## Skip Relationshjps
>	**Input Required**: False

>	**Description**: Allow listed relationships to be skipped in the output returned.


## Include Only Relationships
>	**Input Required**: False

>	**Description**: Include information only about specified relationships.


## Skip Classified Elements
>	**Input Required**: False

>	**Description**: Skip elements with the any of the specified classifications.


## Include Only Classified Elements
>	**Input Required**: False

>	**Description**: Include only elements with the specified classifications.


## Governance Zone Filter
>	**Input Required**: False

>	**Description**: Include only elements in one of the specified governance zones.


## Graph Query Depth
>	**Input Required**: False

>	**Description**: The depth of the hierarchy to return. Default is 5. Specifying 0 returns only the top level attributes. 

>	**Default Value**: 1


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


## Limit Result by Status
>	**Input Required**: False

>	**Description**: One of the status values from a list of valid values.

>	**Valid Values**:  ACTIVE; DELETED; 


## Page Size
>	**Input Required**: False

>	**Description**: The number of elements returned per page.

>	**Default Value**: 0


## Start From
>	**Input Required**: False

>	**Description**: When paging through results, the starting point of the results to return.

>	**Default Value**: 0


## Effective Time
>	**Input Required**: False

>	**Description**: An ISO-8601 string representing the time to use for evaluating effectivity of the elements related to this one.


## Effective From
>	**Input Required**: False

>	**Description**: A string in ISO-8601 format that defines the when an element becomes effective (visible).


## Effective To
>	**Input Required**: False

>	**Description**: A string in ISO-8601 format that defines the when an element is no longer effective (visible).

