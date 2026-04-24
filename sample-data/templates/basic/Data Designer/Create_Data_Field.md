___

## Create Data Field
> Creates or updates a data field — a named, typed element within a data structure. Supports nesting via In Data Field and data class assignment.

### Display Name
>	**Input Required**: True

>	**Attribute Type**: Simple

>	**Description**: The common name of an element.

>	**Alternative Labels**: "Term Name"


### Data Class
>	**Input Required**: False

>	**Attribute Type**: Reference Name

>	**Description**: The data class that specifies the valid values or patterns for this data field (DataValueDefinition relationship).


### Data Type
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: The data type of the field or value specification (e.g. string, int, date, boolean).

>	**Valid Values**: string,int,long,date,boolean,char,byte,float,double,biginteger,bigdecimal,array<string>,array<int>,map<string,string>,map<string,boolean>,map<string,int>,map<string,long>,map<string,double>,map<string,date>,map<string,object>,short,map<string,array<string>>,other

>	**Default Value**: string


### Default Value
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: The default value assigned to this field or data class when no value is supplied.


### In Data Field
>	**Input Required**: False

>	**Attribute Type**: Reference Name

>	**Description**: The data field that this element is nested within (NestedDataField relationship).


### In Data Structure
>	**Input Required**: False

>	**Attribute Type**: Reference Name

>	**Description**: The data structure that contains this data field (MemberDataField relationship).


### Is Nullable
>	**Input Required**: False

>	**Attribute Type**: Bool

>	**Description**: If true, the field may hold null values.

>	**Default Value**: true


### Length
>	**Input Required**: False

>	**Attribute Type**: Simple Int

>	**Description**: The maximum number of characters or digits allowed in the field.


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


### Minimum Length
>	**Input Required**: False

>	**Attribute Type**: Simple Int

>	**Description**: The minimum number of characters or digits required in the field.


### Name Patterns
>	**Input Required**: False

>	**Attribute Type**: Simple List

>	**Description**: Name patterns for naming standard rules.


### Namespace Path
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: The namespace path that qualifies the element's name within a larger naming hierarchy.


### Ordered Values
>	**Input Required**: False

>	**Attribute Type**: Bool

>	**Description**: If true, the values in this field are ordered (i.e. sequence matters).


### Position
>	**Input Required**: False

>	**Attribute Type**: Simple Int

>	**Description**: The ordinal position of the data field within its containing data structure.

>	**Default Value**: 0


### Precision
>	**Input Required**: False

>	**Attribute Type**: Simple Int

>	**Description**: The number of significant digits after the decimal point for numeric fields.


### Sort Order
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: The sort order for values in this field. Valid values from DataItemSortOrder enum: UNKNOWN, UNSORTED, ASCENDING, DESCENDING, OTHER.


### Units
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: The unit of measure for numeric values in this field or specification (e.g. metres, kg, USD).


### Allow Duplicate Values
>	**Input Required**: False

>	**Attribute Type**: Bool

>	**Description**: If true, the data class allows duplicate values in the data field.

>	**Default Value**: true


### Data Class
>	**Input Required**: False

>	**Attribute Type**: Reference Name

>	**Description**: The data class that specifies the valid values or patterns for this data field (DataValueDefinition relationship).


### Data Type
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: The data type of the field or value specification (e.g. string, int, date, boolean).

>	**Valid Values**: string,int,long,date,boolean,char,byte,float,double,biginteger,bigdecimal,array<string>,array<int>,map<string,string>,map<string,boolean>,map<string,int>,map<string,long>,map<string,double>,map<string,date>,map<string,object>,short,map<string,array<string>>,other

>	**Default Value**: string


### Default Value
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: The default value assigned to this field or data class when no value is supplied.


### In Data Field
>	**Input Required**: False

>	**Attribute Type**: Reference Name

>	**Description**: The data field that this element is nested within (NestedDataField relationship).


### In Data Structure
>	**Input Required**: False

>	**Attribute Type**: Reference Name

>	**Description**: The data structure that contains this data field (MemberDataField relationship).


### Is Nullable
>	**Input Required**: False

>	**Attribute Type**: Bool

>	**Description**: If true, the field may hold null values.

>	**Default Value**: true


### Length
>	**Input Required**: False

>	**Attribute Type**: Simple Int

>	**Description**: The maximum number of characters or digits allowed in the field.


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


### Minimum Length
>	**Input Required**: False

>	**Attribute Type**: Simple Int

>	**Description**: The minimum number of characters or digits required in the field.


### Name Patterns
>	**Input Required**: False

>	**Attribute Type**: Simple List

>	**Description**: Name patterns for naming standard rules.


### Ordered Values
>	**Input Required**: False

>	**Attribute Type**: Bool

>	**Description**: If true, the values in this field are ordered (i.e. sequence matters).


### Position
>	**Input Required**: False

>	**Attribute Type**: Simple Int

>	**Description**: The ordinal position of the data field within its containing data structure.

>	**Default Value**: 0


### Precision
>	**Input Required**: False

>	**Attribute Type**: Simple Int

>	**Description**: The number of significant digits after the decimal point for numeric fields.


### Sort Order
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: The sort order for values in this field. Valid values from DataItemSortOrder enum: UNKNOWN, UNSORTED, ASCENDING, DESCENDING, OTHER.


### Units
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: The unit of measure for numeric values in this field or specification (e.g. metres, kg, USD).


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


### Qualified Name
>	**Input Required**: False

>	**Attribute Type**: QN

>	**Description**: The unique, text name of an element.


### Content Status
>	**Input Required**: False

>	**Attribute Type**: Valid Value

>	**Description**: The lifecycle status of an element.

>	**Valid Values**: DRAFT,PREPARED,PROPOSED,APPROVED,REJECTED,ACTIVE,DEPRECATED,OTHER

>	**Default Value**: ACTIVE


### Aliases
>	**Input Required**: False

>	**Attribute Type**: Simple List

>	**Description**: Alternative names for this  field, used in different systems or contexts.

>	**Alternative Labels**: Alias


### Aliases
>	**Input Required**: False

>	**Attribute Type**: Simple List

>	**Description**: Alternative names for this  field, used in different systems or contexts.

>	**Alternative Labels**: Alias


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


### Authors
>	**Input Required**: False

>	**Attribute Type**: Simple List

>	**Description**: The authors.


___
