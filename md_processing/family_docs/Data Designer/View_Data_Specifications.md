# **View Data Specifications**
>	Return the data specifications, optionally filtered by the search string.

## **Search String**
>	**Input Required**: False

>	**Description**: An optional search string to filter results by.

>	**Alternative Labels**: Filter

>	**Default Value**: *


## **Output Format**
>	**Input Required**: False

>	**Description**: Optional specification of output format for the query.

>	**Alternative Labels**: Format

>	**Valid Values**: LIST; FORM; DICT; MD; MERMAID; REPORT

>	**Default Value**: LIST


## **Starts With**
>	**Input Required**: False

>	**Description**: If true, look for matches with the search string starting from the beginning of  a field.

>	**Default Value**: True


## **Ends With**
>	**Input Required**: False

>	**Description**: If true, look for matches with the search string starting from the end of  a field.

>	**Default Value**: False


## **Ignore Case**
>	**Input Required**: False

>	**Description**: If true, ignore the difference between upper and lower characters when matching the search string.

>	**Default Value**: False


## **AsOfTime**
>	**Input Required**: False

>	**Description**: An ISO-8601 string representing the time to view the state of the repository.

>	**Alternative Labels**: As Of Time


## **Sort Order**
>	**Input Required**: False

>	**Description**: How to order the results. The sort order can be selected from a list of valid value.

>	**Valid Values**: ANY; CREATION_DATE_RECENT; CREATION_DATA_OLDEST; LAST_UPDATE_RECENT; LAST_UPDATE_OLDEST; PROPERTY_ASCENDING; PROPERTY_DESCENDING


## **Page Size**
>	**Input Required**: False

>	**Description**: The number of elements returned per page.


## **Start From**
>	**Input Required**: False

>	**Description**: When paging through results, the starting point of the results to return.

>	**Default Value**: 0

