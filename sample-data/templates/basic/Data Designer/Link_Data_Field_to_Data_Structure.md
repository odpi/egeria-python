___

## Link Data Field to Data Structure
> Add a data field to a data structure (MemberDataField relationship), optionally with its position, cardinality and coverage category within the structure.
>
>	**Alternative Names**: Detach Data Field from Data Structure; Link Data Field to Structure; Link Field to Structure

### Data Structure
>	**Input Required**: True

>	**Attribute Type**: Reference Name

>	**Description**: A data structure name. Preferably a qualified name.


### Data Field
>	**Input Required**: True

>	**Attribute Type**: Reference Name

>	**Description**: A data field  name. Preferably a qualified name.


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

>	**Description**: The ordinal position: of a data field within its containing data structure, or of a data value among an element's processing variables or a parent value's embedded values (0 means unset).

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


___
