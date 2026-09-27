___

## Link Nested Data Field
> Nest a data field under a parent data field (NestedDataField relationship), optionally with its position, cardinality and coverage category within the parent.
>
>	**Alternative Names**: Link Data Field to Parent Data Field

### Label
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: A label used to identify or categorise a relationship link.

>	**Alternative Labels**: Wire Label


### Maximum Cardinality
>	**Input Required**: False

>	**Attribute Type**: Simple Int

>	**Description**: The maximum number of times this field may appear in the containing data structure (-1 means unbounded).

>	**Default Value**: 1


### Minimum Cardinality
>	**Input Required**: False

>	**Attribute Type**: Simple Int

>	**Description**: The minimum number of times this field must appear in the containing data structure.

>	**Default Value**: 1


### Position
>	**Input Required**: False

>	**Attribute Type**: Simple Int

>	**Description**: The ordinal position of the data field within its containing data structure.

>	**Default Value**: 0


### Journal Entry
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: A text entry into a journal.


### Description
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: A description.


### Coverage Category
>	**Input Required**: False

>	**Attribute Type**: Valid Value

>	**Description**: How the values of the linked data field cover the domain of possible values (CoverageCategory enum).

>	**Valid Values**: UNKNOWN,UNIQUE_IDENTIFIER,IDENTIFIER,CORE_DETAIL,EXTENDED_DETAIL


### Parent Data Field
>	**Input Required**: False

>	**Attribute Type**: Reference Name

>	**Description**: The parent data field in a NestedDataField relationship.


### Nested Data Field
>	**Input Required**: False

>	**Attribute Type**: Reference Name

>	**Description**: The data field nested under the parent data field (NestedDataField relationship).


___
