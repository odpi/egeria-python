# Create Data Field
>	A data field is a fundamental building block for a data structure.

## Display Name
>	**Input Required**: True

>	**Description**: Name of the Data Field

>	**Alternative Labels**: Name; Data Field Name


## Description
>	**Input Required**: False

>	**Description**: A description of the Data Field


## Data Type
>	**Input Required**: True

>	**Description**: The data type of the data field. Point to data type valid value list if exists.

>	**Valid Values**: string; int; long; date; boolean; char; byte; float; double; biginteger; bigdecimal; array<string>; array<int>; map<string,string>; map<string, boolean>; map<string, int>; map<string, long>; map<string,double>; map<string, date> map<string, object>; short; map<string, array<string>>; other

>	**Default Value**: string


## Position
>	**Input Required**: False

>	**Description**: Position of the data field in the data structure. If 0, position is irrelevant.

>	**Default Value**: 0


## Minimum Cardinality
>	**Input Required**: False

>	**Description**: The minimum cardinality for a data element.

>	**Alternative Labels**: Min Cardinality; min cardinality

>	**Default Value**: 1


## Maximum Cardinality
>	**Input Required**: False

>	**Description**: The maximum cardinality for a data element.

>	**Alternative Labels**: max cardinality; Max Cardinality

>	**Default Value**: 1


## In Data Structure
>	**Input Required**: False

>	**Description**: The data structure this field is a member of. If display name is not unique, use qualified name.

>	**Alternative Labels**: Data Structure


## In Data Dictionary
>	**Input Required**: False

>	**Description**: What data dictionaries is this data field in?


## Data Class
>	**Input Required**: False

>	**Description**: The data class that values of this data field conform to.


## Aliases
>	**Input Required**: False

>	**Description**: 


## Name Patterns
>	**Input Required**: False

>	**Description**: Name patterns  for the field.


## Namespace
>	**Input Required**: False

>	**Description**: Optional namespace that scopes the field.


## isNullable
>	**Input Required**: False

>	**Description**: Can the values within the dataclass be absent?

>	**Alternative Labels**: Nullable

>	**Default Value**: true


## Minimum Length
>	**Input Required**: False

>	**Description**: 

>	**Alternative Labels**: Min Length


## Length
>	**Input Required**: False

>	**Description**: The length of a value for a field.


## Precision
>	**Input Required**: False

>	**Description**: The precision of a numeric


## Ordered Values
>	**Input Required**: False

>	**Description**: is this field in an ordered list?


## Units
>	**Input Required**: False

>	**Description**: An optional string indicating the units of the field.

>	**Alternative Labels**: gradians


## Sort Order
>	**Input Required**: False

>	**Description**: Method by which this field should be sorted?


## Default Value
>	**Input Required**: False

>	**Description**: Specify a default value for the data class.

>	**Alternative Labels**: Default


## User Defined Status
>	**Input Required**: False

>	**Description**: Only valid if Product Status is set to OTHER. User defined & managed status values.


## Category
>	**Input Required**: False

>	**Description**: A user specified category name that can be used for example, to define product types or agreement types.

>	**Alternative Labels**: Category Name


## Version Identifier
>	**Input Required**: False

>	**Description**: Published product version identifier.

>	**Default Value**: 1.0


## URL
>	**Input Required**: False

>	**Description**: Link to supporting information


## Identifier
>	**Input Required**: False

>	**Description**: role identifier


## Classifications
>	**Input Required**: false

>	**Description**: Optionally specify the initial classifications for a collection. Multiple classifications can be specified. 

>	**Alternative Labels**: classification


## Is Own Anchor
>	**Input Required**: False

>	**Description**: Generally True. 

>	**Alternative Labels**: Own Anchor

>	**Default Value**: True


## Anchor ID
>	**Input Required**: False

>	**Description**: Anchor identity for the collection. Typically a qualified name but if display name is unique then it could be used (not recommended)


## Parent ID
>	**Input Required**: False

>	**Description**: Unique name of the parent element.

>	**Alternative Labels**: Parent;


## Parent Relationship Type Name
>	**Input Required**: False

>	**Description**: The kind of the relationship to the parent element.


## Anchor Scope Name
>	**Input Required**: False

>	**Description**: Optional qualified name of an anchor scope.


## Parent at End1
>	**Input Required**: False

>	**Description**: Is the parent at end1 of the relationship?

>	**Default Value**: True


## Qualified Name
>	**Input Required**: False

>	**Description**: A unique qualified name for the element. Generated using the qualified name pattern  if not user specified.


## GUID
>	**Input Required**: False

>	**Description**: A system generated unique identifier.

>	**Alternative Labels**: Guid; guid


## Effective Time
>	**Input Required**: False

>	**Description**: An ISO-8601 string representing the time to use for evaluating effectivity of the elements related to this one.


## Effective From
>	**Input Required**: False

>	**Description**: A string in ISO-8601 format that defines the when an element becomes effective (visible).


## Effective To
>	**Input Required**: False

>	**Description**: A string in ISO-8601 format that defines the when an element is no longer effective (visible).


## Merge Update
>	**Input Required**: False

>	**Description**: If True, only those attributes specified in the update will be updated; If False, any attributes not provided during the update will be set to None.

>	**Alternative Labels**: Merge

>	**Default Value**: True


## Additional Properties
>	**Input Required**: False

>	**Description**: Additional user defined values organized as name value pairs in a dictionary.


## External Source GUID
>	**Input Required**: False

>	**Description**: Identifier of an external source that is associated with this element.


## External Source Name
>	**Input Required**: False

>	**Description**: Name of an external element that is associated with this element.


## Journal Entry
>	**Input Required**: False

>	**Description**: 


## URL
>	**Input Required**: False

>	**Description**: Link to supporting information


## Search Keywords
>	**Input Required**: False

>	**Description**: Keywords to facilitate finding the element


## Supplementary Properties
>	**Input Required**: False

>	**Description**: Provide supplementary information to the element using the structure of a glossary term

