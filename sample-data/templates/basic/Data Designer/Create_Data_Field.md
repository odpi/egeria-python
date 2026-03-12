# Create Data Field
> Creates or updates a data field — a named, typed element within a data structure. Supports nesting via In Data Field and data class assignment.

# Required

## Display Name
>	**Input Required**: True

>	**Description**: The common name of an element.

>	**Alternative Labels**: "Term Name"


# Data Field Properties

## Aliases
>	**Input Required**: False

>	**Description**: Alternative names for this data field, used in different systems or contexts.


## Allow Duplicate Values
>	**Input Required**: False

>	**Description**: If true, the data class allows duplicate values in the data field.

>	**Default Value**: true


## Data Class
>	**Input Required**: False

>	**Description**: The data class that specifies the valid values or patterns for this data field (DataValueDefinition relationship).


## Data Type
>	**Input Required**: False

>	**Description**: The data type of the field or value specification (e.g. string, int, date, boolean).

>	**Valid Values**: string,int,long,date,boolean,char,byte,float,double,biginteger,bigdecimal,array<string>,array<int>,map<string,string>,map<string,boolean>,map<string,int>,map<string,long>,map<string,double>,map<string,date>,map<string,object>,short,map<string,array<string>>,other

>	**Default Value**: string


## Default Value
>	**Input Required**: False

>	**Description**: The default value assigned to this field or data class when no value is supplied.


## In Data Field
>	**Input Required**: False

>	**Description**: The data field that this element is nested within (NestedDataField relationship).


## In Data Structure
>	**Input Required**: False

>	**Description**: The data structure that contains this data field (MemberDataField relationship).


## Is Nullable
>	**Input Required**: False

>	**Description**: If true, the field may hold null values.

>	**Default Value**: true


## Length
>	**Input Required**: False

>	**Description**: The maximum number of characters or digits allowed in the field.


## Maximum Cardinality
>	**Input Required**: False

>	**Description**: The maximum number of times this field may appear in the containing data structure (-1 means unbounded).

>	**Default Value**: 1


## Minimum Cardinality
>	**Input Required**: False

>	**Description**: The minimum number of times this field must appear in the containing data structure.

>	**Default Value**: 1


## Minimum Length
>	**Input Required**: False

>	**Description**: The minimum number of characters or digits required in the field.


## Name Patterns
>	**Input Required**: False

>	**Description**: Name patterns for naming standard rules.


## Ordered Values
>	**Input Required**: False

>	**Description**: If true, the values in this field are ordered (i.e. sequence matters).


## Position
>	**Input Required**: False

>	**Description**: The ordinal position of the data field within its containing data structure.

>	**Default Value**: 0


## Precision
>	**Input Required**: False

>	**Description**: The number of significant digits after the decimal point for numeric fields.


## Sort Order
>	**Input Required**: False

>	**Description**: The sort order for values in this field. Valid values from DataItemSortOrder enum: UNKNOWN, UNSORTED, ASCENDING, DESCENDING, OTHER.


## Units
>	**Input Required**: False

>	**Description**: The unit of measure for numeric values in this field or specification (e.g. metres, kg, USD).


# Common Properties

## Journal Entry
>	**Input Required**: False

>	**Description**: A text entry into a journal.


## Category
>	**Input Required**: False

>	**Description**: A user-defined category for the element, used to group related elements for display or search purposes.

>	**Alternative Labels**: Category Name


## Description
>	**Input Required**: False

>	**Description**: A description.


## Qualified Name
>	**Input Required**: False

>	**Description**: The unique, text name of an element.


## Content Status
>	**Input Required**: False

>	**Description**: The lifecycle status of an element.

>	**Valid Values**: DRAFT,PREPARED,PROPOSED,APPROVED,REJECTED,ACTIVE,DEPRECATED,OTHER

>	**Default Value**: ACTIVE


# Additional Properties

## Search Keywords
>	**Input Required**: False

>	**Description**: A list of search keywords.


## GUID
>	**Input Required**: False

>	**Description**: A unique identifier - typically of an element in this context.

>	**Alternative Labels**: Guid; guid


## Identifier
>	**Input Required**: False

>	**Description**: An identier


## URL
>	**Input Required**: False

>	**Description**: URL for further information.


## Version Identifier
>	**Input Required**: False

>	**Description**: The version of the element

>	**Alternative Labels**: Version

>	**Default Value**: 1.0


## Authors
>	**Input Required**: False

>	**Description**: The authors.

